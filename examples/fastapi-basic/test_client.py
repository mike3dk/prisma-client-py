#!/usr/bin/env python3
"""
Simple test to verify Prisma client works with 6.8.2
"""

import asyncio
from prisma import Prisma


async def main():
    print('🔧 Testing Prisma Client with 6.8.2...')

    client = Prisma()
    await client.connect()

    print('✅ Connected to database successfully')

    # Test creating a user
    user = await client.user.create({'name': 'Test User', 'email': 'test@example.com'})
    print(f'✅ Created user: {user.name} (ID: {user.id})')

    # Test creating a post
    post = await client.post.create({'title': 'Test Post', 'published': True, 'author_id': user.id})
    print(f'✅ Created post: {post.title} (ID: {post.id})')

    # Test querying
    users = await client.user.find_many(include={'posts': True})
    print(f'✅ Found {len(users)} users')
    for u in users:
        post_count = len(u.posts) if u.posts else 0
        print(f'   - {u.name} has {post_count} posts')

    # Clean up
    await client.post.delete_many()
    await client.user.delete_many()
    print('✅ Cleaned up test data')

    await client.disconnect()
    print('✅ Disconnected from database')

    print('\n🎉 All Prisma client tests passed with version 6.8.2!')


if __name__ == '__main__':
    asyncio.run(main())
